import std.math;
import std.typecons;
import std.algorithm;
import std.ascii;
string f(string chars) 
{
    string s = "";
    foreach (ch; chars) {
        if (count(chars, ch) % 2 == 0) {
            s ~= toUpper(ch);
        } else {
            s ~= ch;
        }
    }
    return s;
}
unittest
{
    alias candidate = f;

    assert(candidate("acbced") == "aCbCed");
}
void main(){}
