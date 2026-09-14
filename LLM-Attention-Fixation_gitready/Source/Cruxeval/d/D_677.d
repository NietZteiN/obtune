import std.math;
import std.typecons;
string f(string text, long length) 
{
    length = length < 0 ? -length : length;
    string output = "";
    foreach (idx; 0..length)
    {
        if (text[idx % text.length] != ' ')
        {
            output ~= text[idx % text.length];
        }
        else
        {
            break;
        }
    }
    return output;
}
unittest
{
    alias candidate = f;

    assert(candidate("I got 1 and 0.", 5L) == "I");
}
void main(){}
