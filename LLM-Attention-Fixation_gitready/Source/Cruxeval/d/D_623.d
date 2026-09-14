import std.math;
import std.typecons;
import std.string;

string f(string text, string[] rules) 
{
    foreach (rule; rules)
    {
        if (rule == "@")
        {
            text = text[$-1 .. 0];
        }
        else if (rule == "~")
        {
            text = text.toUpper();
        }
        else if (text.length > 0 && text[$-1] == rule[0])
        {
            text = text[0 .. $-1];
        }
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("hi~!", ["~", "`", "!", "&"]) == "HI~");
}
void main(){}
