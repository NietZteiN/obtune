import std.math;
import std.typecons;
import std.ascii;

string f(string text) 
{
    string result = "";
    foreach(i; 0 .. text.length) {
        if (i % 2 == 0) {
            result ~= toUpper(text[i]);
        } else {
            result ~= text[i];
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("vsnlygltaw") == "VsNlYgLtAw");
}
void main(){}
