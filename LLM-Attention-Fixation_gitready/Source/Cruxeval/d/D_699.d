import std.math;
import std.typecons;
import std.algorithm;
import std.array;

string[] f(string text, string elem) 
{
    if (elem != "") {
        while (text.startsWith(elem)) {
            text = text.replace(elem, "");
        }
        while (elem.startsWith(text)) {
            elem = elem.replace(text, "");
        }
    }
    return [elem, text];
}
unittest
{
    alias candidate = f;

    assert(candidate("some", "1") == ["1", "some"]);
}
void main(){}
