import std.math;
import std.typecons;
import std.ascii;

string f(string text) 
{
    foreach_reverse(i; 0 .. text.length) {
        if (!isUpper(text[i])) {
            return text[0 .. i];
        }
    }
    return "";
}
unittest
{
    alias candidate = f;

    assert(candidate("SzHjifnzog") == "SzHjifnzo");
}
void main(){}
