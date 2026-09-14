import std.math;
import std.typecons;
import std.string;

string f(string text, string new_value, size_t index) 
{
    if (index >= text.length)
        throw new Exception("Index out of range");

    return text[0 .. index] ~ new_value ~ text[index + 1 .. $];
}
unittest
{
    alias candidate = f;

    assert(candidate("spain", "b", 4L) == "spaib");
}
void main(){}
