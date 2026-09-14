import std.math;
import std.typecons;
import std.conv;
import std.array;

string f(string text, string value) 
{
    auto new_text = text.dup;
    new_text ~= value; // Append value to new_text
    auto length = new_text.length; // Get the length of new_text
    return "[" ~ length.text ~ "]"; // Return the length as a string
}

unittest
{
    alias candidate = f;

    assert(candidate("abv", "a") == "[4]");
}
void main(){}
