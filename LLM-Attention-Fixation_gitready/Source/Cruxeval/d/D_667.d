import std.math;
import std.typecons;
import std.conv;
string[] f(string text) 
{
    string[] new_text;
    foreach (i; 0 .. text.length / 3) {
        new_text ~= "< " ~ text[i * 3 .. i * 3 + 3] ~ " level=" ~ to!string(i) ~ " >";
    }
    string last_item = text[text.length / 3 * 3 .. $];
    new_text ~= "< " ~ last_item ~ " level=" ~ to!string(text.length / 3) ~ " >";
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate("C7") == ["< C7 level=0 >"]);
}
void main(){}
