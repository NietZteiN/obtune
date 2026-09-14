import std.math;
import std.typecons;
import std.string;
import std.ascii : isAlpha, isDigit;

string f(string text) 
{
    string new_text = "";
    foreach (ch; text)
    {
        if (isDigit(ch) || (ch == 'ä' || ch == 'Ä' || ch == 'ï' || ch == 'Ï' || ch == '�' || ch == 'Ö' || ch == '�' || ch == 'Ü'))
        {
            new_text ~= ch;
        }
    }
    return new_text;
}
unittest
{
    alias candidate = f;

    assert(candidate("") == "");
}
void main(){}
