import std.math;
import std.typecons;
import std.string;
import std.array;

string f(string text, string search_chars, string replace_chars) 
{
    auto trans_table = std.string.makeTrans(search_chars, replace_chars);
    string result = "";
    foreach (char c; text)
    {
        result ~= trans_table[c];
    }
    return result;
}
unittest
{
    alias candidate = f;

    assert(candidate("mmm34mIm", "mm3", ",po") == "pppo4pIp");
}
void main(){}
