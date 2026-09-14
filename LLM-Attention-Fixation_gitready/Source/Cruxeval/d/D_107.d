import std.math;
import std.typecons;
import std.string;

string f(string text) 
{
    string result = "";
    foreach (i, c; text)
    {
        if (c >= ' ' && c <= '~')
        {
            if (c >= 'a' && c <= 'z')
            {
                result ~= c.toUpper();
            } 
            else 
            {
                result ~= c;
            }
        } 
        else 
        {
            return "False";
        }
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("ua6hajq") == "UA6HAJQ");
}
void main(){}
