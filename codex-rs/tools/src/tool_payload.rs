use std::borrow::Cow;

use codex_protocol::models::SearchToolCallParams;

/// Canonical payload shapes accepted by model-visible tool runtimes.
#[derive(Clone, Debug, PartialEq)]
pub enum ToolPayload {
    Function { arguments: String },
    ToolSearch { arguments: SearchToolCallParams },
    Custom { input: String },
}

impl ToolPayload {
    pub fn log_payload(&self) -> Cow<'_, str> {
        match self {
            ToolPayload::Function { arguments } => Cow::Borrowed(arguments),
            ToolPayload::ToolSearch { arguments } => Cow::Owned(arguments.query.clone()),
            ToolPayload::Custom { input } => Cow::Borrowed(input),
        }
    }
}

/// Parameter name used when a freeform (grammar) tool is advertised to a
/// provider that rejects `type: "custom"` tool entries.
///
/// The tool body then travels as a JSON string argument under this key, and
/// [`freeform_source_from_arguments`] unwraps it back to raw text on dispatch.
pub const FREEFORM_SOURCE_PARAMETER: &str = "input";

/// Recover the raw tool body from function-call arguments produced by a
/// freeform tool that was downgraded to a function tool.
///
/// Accepts `{"input": "<source>"}`. A bare JSON string, and the empty
/// argument string, are also accepted so a provider that forwards the body
/// unquoted still works.
pub fn freeform_source_from_arguments(arguments: &str) -> Result<String, String> {
    let trimmed = arguments.trim();
    if trimmed.is_empty() {
        return Ok(String::new());
    }

    let value: serde_json::Value = serde_json::from_str(trimmed).map_err(|error| {
        format!("failed to parse function arguments: {error}. Send the tool input as a single JSON string, for example {{\"input\": \"<source>\"}}.")
    })?;

    match value {
        serde_json::Value::String(source) => Ok(source),
        serde_json::Value::Object(map) => match map.get(FREEFORM_SOURCE_PARAMETER) {
            Some(serde_json::Value::String(source)) => Ok(source.clone()),
            Some(other) => Err(format!(
                "`{FREEFORM_SOURCE_PARAMETER}` must be a JSON string, got {other}."
            )),
            None => Err(format!(
                "missing `{FREEFORM_SOURCE_PARAMETER}` in function arguments. Send the tool input as {{\"{FREEFORM_SOURCE_PARAMETER}\": \"<source>\"}}."
            )),
        },
        other => Err(format!(
            "expected a JSON string or an object with `{FREEFORM_SOURCE_PARAMETER}`, got {other}."
        )),
    }
}
