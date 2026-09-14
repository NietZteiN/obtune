import std.math;
import std.typecons;
import std.array;
import std.ascii;

string f(string item) 
{
    string modified = item.replace(". ", " , ").replace("&#33; ", "! ").replace(". ", "? ").replace(". ", ". ");
    return toUpper(modified[0]) ~ modified[1 .. $];
}
unittest
{
    alias candidate = f;

    assert(candidate(".,,,,,. منبت") == ".,,,,, , منبت");
}
void main(){}
