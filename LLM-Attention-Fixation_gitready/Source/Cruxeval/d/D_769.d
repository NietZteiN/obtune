import std.algorithm;
import std.array;
import std.string;
import std.ascii : isUpper, isLower, toLower, toUpper;

string f(string text) {
    char[] text_list = text.dup;
    foreach (i, ref char c; text_list) {
        if (isUpper(c)) {
            c = toLower(c);
        } else if (isLower(c)) {
            c = toUpper(c);
        }
    }
    return text_list.idup;
}

unittest
{
    alias candidate = f;

    assert(candidate("akA?riu") == "AKa?RIU");
}
void main(){}
