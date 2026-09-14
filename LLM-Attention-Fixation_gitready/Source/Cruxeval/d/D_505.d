import std.math;
import std.typecons;
import std.ascii;

string f(string string) 
{
    while (string.length > 0) {
        if (isAlpha(string[string.length - 1])) {
            return string;
        }
        string = string[0 .. $-1];
    }
    return string;
}
unittest
{
    alias candidate = f;

    assert(candidate("--4/0-209") == "");
}
void main(){}
