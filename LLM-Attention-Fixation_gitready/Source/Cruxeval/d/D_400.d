import std.math;
import std.typecons;
import std.string;
import std.algorithm;
import std.array;
import std.conv;

string f(string multi_string) 
{
    auto splitString = multi_string.split();
    string[] asciiStrings;

    foreach (str; splitString)
    {
        bool isAscii = true;
        foreach (ch; str)
        {
            if (ch < 0 || ch > 127)
            {
                isAscii = false;
                break;
            }
        }
        if (isAscii)
        {
            asciiStrings ~= str;
        }
    }

    return asciiStrings.join(", ");
}

unittest
{
    alias candidate = f;

    assert(candidate("I am hungry! eat food.") == "I, am, hungry!, eat, food.");
}
void main(){}
