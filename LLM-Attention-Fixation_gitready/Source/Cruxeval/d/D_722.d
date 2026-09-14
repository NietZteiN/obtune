import std.algorithm;
import std.string;
import std.uni;

string f(string text) {
    char[] result;
    foreach (char c; text) {
        if (isUpper(c)) {
            result ~= toLower(c);
        } else {
            result ~= toUpper(c);
        }
    }
    return result.idup; // Convert mutable char[] back to immutable string
}

unittest
{
    alias candidate = f;

    assert(candidate(",wPzPppdl/") == ",WpZpPPDL/");
}
void main(){}
