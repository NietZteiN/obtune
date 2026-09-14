import std.math;
import std.typecons;
import std.algorithm;

string f(string text, string suffix) 
{
    if (suffix.startsWith("/")) {
        return text ~ suffix[1..$];
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("hello.txt", "/") == "hello.txt");
}
void main(){}
