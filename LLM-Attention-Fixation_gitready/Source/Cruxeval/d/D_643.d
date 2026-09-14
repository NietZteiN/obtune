import std.math;
import std.typecons;
import std.algorithm;
import std.range;
import std.ascii;
import std.string;

string f(string text, string suffix) 
{
    if (text.endswith(suffix))
    {
        auto lastChar = text[$ - 1..$];
        if (isLower(lastChar[0]))
        {
            lastChar = toUpper(lastChar);
        }
        else
        {
            lastChar = toLower(lastChar);
        }
        text = text[0..$ - 1] ~ lastChar;
    }
    return text;
}

bool endswith(string text, string suffix)
{
    return text[$ - suffix.length..$] == suffix;
}

unittest
{
    alias candidate = f;

    assert(candidate("damdrodm", "m") == "damdrodM");
}
void main(){}
