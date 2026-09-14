import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    auto mid = (text.length - 1) / 2;
    string result;
    for (size_t i = 0; i < mid; i++)
    {
        result ~= text[i];
    }
    for (size_t i = mid; i < text.length - 1; i++)
    {
        result ~= text[mid + text.length - 1 - i];
    }
    while (result.length < text.length)
    {
        result ~= text[text.length - 1];
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("eat!") == "e!t!");
}
void main(){}
