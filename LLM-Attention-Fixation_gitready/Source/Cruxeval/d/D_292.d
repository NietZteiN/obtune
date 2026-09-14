import std.math;
import std.typecons;
string f(string text) 
{
    string new_text;
    foreach (char c; text)
    {
        if (c >= '0' && c <= '9')
        {
            new_text ~= c;
        }
        else
        {
            new_text ~= '*';
        }
    }
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate("5f83u23saa") == "5*83*23***");
}
void main(){}
