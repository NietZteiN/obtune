import std.algorithm;
import std.array;
import std.string;

string f(string text, string pref) {
    if (text.startsWith(pref)) {
        size_t n = pref.length;
        string[] parts = text[n..$].split('.');
        string[] prefParts = text[0..n].split('.');
        text = parts[1..$].join(".") ~ (parts.length > 1 && prefParts.length > 1 ? "." : "") ~ prefParts[0..$-1].join(".");
    }
    return text;
}

unittest
{
    alias candidate = f;

    assert(candidate("omeunhwpvr.dq", "omeunh") == "dq");
}
void main(){}
