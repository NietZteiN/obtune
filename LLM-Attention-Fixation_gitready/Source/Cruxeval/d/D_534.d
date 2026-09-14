import std.math;
import std.typecons;
import std.algorithm;
import std.range;
import std.string;

string f(string sequence, string value) 
{
    auto i = sequence.indexOf(value) - sequence.length / 3;
    i = i > 0 ? i : 0;
    string result = "";
    foreach (j, v; sequence[i .. $])
    {
        if (v == '+')
            result ~= value;
        else
            result ~= sequence[i + j];
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("hosu", "o") == "hosu");
}
void main(){}
