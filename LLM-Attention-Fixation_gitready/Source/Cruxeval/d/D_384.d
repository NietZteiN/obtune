import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.range;
import std.string;

string f(string text, string chars) 
{
    auto new_text = text;
    while (new_text.length > 0 && text.length > 0) {
        if (canFind(chars, new_text[0])) {
            new_text = new_text[1..$];
        } else {
            break;
        }
    }
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate("asfdellos", "Ta") == "sfdellos");
}
void main(){}
