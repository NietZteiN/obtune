import std.math;
import std.typecons;
import std.conv;
import std.string;

string f(string text) 
{
    string new_text = "";
    foreach (i, character; text)
    {
        new_text ~= toUpper(character) == character ? toLower(character) : toUpper(character);
    }
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate("dst vavf n dmv dfvm gamcu dgcvb.") == "DST VAVF N DMV DFVM GAMCU DGCVB.");
}
void main(){}
