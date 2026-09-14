import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text, string separator) 
{
    return text.split(separator).join(" ");
}
unittest
{
    alias candidate = f;

    assert(candidate("a", "a") == " ");
}
void main(){}
