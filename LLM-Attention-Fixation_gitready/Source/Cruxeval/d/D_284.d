import std.math;
import std.typecons;
string f(string text, string prefix) 
{
    size_t idx = 0;
    foreach (letter; prefix)
    {
        if (text[idx] != letter)
        {
            return null;
        }
        idx++;
    }
    return text[idx..$];
}
unittest
{
    alias candidate = f;

    assert(candidate("bestest", "bestest") == "");
}
void main(){}
