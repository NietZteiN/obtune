import std.math;
import std.typecons;
import std.string;
import std.conv;
import std.algorithm;
import std.array;

string f(string text, string value) 
{
    char[] indexes;
    foreach (i, ch; text)
    {
        if (ch == value[0])
        {
            indexes ~= ch;
        }
    }
    auto new_text = text.replace(value, "");
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate("scedvtvotkwqfoqn", "o") == "scedvtvtkwqfqn");
}
void main(){}
