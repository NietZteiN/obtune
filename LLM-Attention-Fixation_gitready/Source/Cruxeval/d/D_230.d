import std.math;
import std.typecons;
import std.ascii;

string f(string text) 
{
    string result = "";
    long i = text.length - 1;
    while (i >= 0) {
        char c = text[i];
        if (isAlpha(c)) {
            result ~= c;
        }
        i--;
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("102x0zoq") == "qozx");
}
void main(){}
