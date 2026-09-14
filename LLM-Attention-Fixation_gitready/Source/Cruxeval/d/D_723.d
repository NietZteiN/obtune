import std.math;
import std.typecons;
import std.string;
import std.array;

string[] f(string text, long separator) 
{
    if (separator != 0)
    {
        auto splitted = text.splitLines;
        string[] result;
        foreach (line; splitted)
        {
            result ~= line.split("").join(" ");
        }
        return result;
    }
    else
    {
        return text.splitLines;
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("dga nqdkull qcha kl", 1L) == ["d g a   n q d k", "u l l   q c h a   k l"]);
}
void main(){}
