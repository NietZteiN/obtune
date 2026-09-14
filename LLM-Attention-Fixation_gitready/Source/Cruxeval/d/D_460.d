import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string text, long amount) 
{
    auto length = text.length;
    string pre_text = "|";
    if (amount >= length) {
        long extra_space = amount - length;
        pre_text ~= " ".replicate(extra_space / 2);
        return pre_text ~ text ~ pre_text;
    }
    return text;
}
unittest
{
    alias candidate = f;

    assert(candidate("GENERAL NAGOOR", 5L) == "GENERAL NAGOOR");
}
void main(){}
