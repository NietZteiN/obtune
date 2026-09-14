import std.math;
import std.typecons;
string f(string text, string insert) 
{
    string clean = "";
    foreach (char c; text) {
        if (c == '\t' || c == '\r' || c == '\v' || c == ' ' || c == '\f' || c == '\n') {
            clean ~= insert;
        } else {
            clean ~= c;
        }
    }
    return clean;
}
unittest
{
    alias candidate = f;

    assert(candidate("pi wa", "chi") == "pichiwa");
}
void main(){}
