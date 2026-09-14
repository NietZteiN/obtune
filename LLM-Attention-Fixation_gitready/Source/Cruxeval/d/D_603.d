import std.math;
import std.typecons;
import std.array;
import std.string;

string f(string sentences) 
{
    bool oscillating = true;
    foreach (sentence; sentences.split('.'))
    {
        if (!sentence.isNumeric)
        {
            oscillating = false;
            break;
        }
    }
    
    if (oscillating)
    {
        return "oscillating";
    }
    else
    {
        return "not oscillating";
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("not numbers") == "not oscillating");
}
void main(){}
