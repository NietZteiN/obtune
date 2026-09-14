import std.math;
import std.typecons;
import std.ascii;

string f(string text) 
{
    string result = "";
    foreach (char c; text) {
        if (isDigit(c)) {
            result = c ~ result;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("--4yrw 251-//4 6p") == "641524");
}
void main(){}
