import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text) 
{
    auto words = text.split(' ');
    foreach (word; words)
    {
        if (!word.isNumeric)
        {
            return "no";
        }
    }
    return "yes";
}
unittest
{
    alias candidate = f;

    assert(candidate("03625163633 d") == "no");
}
void main(){}
