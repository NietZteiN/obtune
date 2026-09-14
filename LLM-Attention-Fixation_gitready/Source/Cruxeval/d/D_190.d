import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    string result = "";
    foreach (c; text)
    {
        if ('a' <= c && c <= 'z')
        {
            result ~= c;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("980jio80jic kld094398IIl ") == "jiojickldl");
}
void main(){}
