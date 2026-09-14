import std.math;
import std.typecons;
import std.string;
import std.ascii;
import std.algorithm;

string f(string text) 
{
    if (text.length > 0 && text.toUpper() == text) {
        auto cs = text.translate(dup("ABCDEFGHIJKLMNOPQRSTUVWXYZ"), dup("abcdefghijklmnopqrstuvwxyz"));
        return text.translate(cs);
    }
    return text.toLower()[0 .. min(3, text.length)];
}
unittest
{
    alias candidate = f;

    assert(candidate("mTYWLMwbLRVOqNEf.oLsYkZORKE[Ko[{n") == "mty");
}
void main(){}
