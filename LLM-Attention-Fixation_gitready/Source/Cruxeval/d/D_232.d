import std.math;
import std.typecons;
import std.string;
import std.range;

string f(string text, string changes) 
{
    string result = "";
    int count = 0;
    foreach (c; text)
    {
        if (c == 'e')
        {
            result ~= c;
        }
        else
        {
            result ~= changes[count % changes.length];
            count++;
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("fssnvd", "yes") == "yesyes");
}
void main(){}
