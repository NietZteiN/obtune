import std.math;
import std.typecons;
string f(string text) 
{
    string nums;
    foreach (char c; text)
    {
        if (c >= '0' && c <= '9')
        {
            nums ~= c;
        }
    }
    
    assert(nums.length > 0, "No numeric characters found in the text.");
    
    return nums;
}
unittest
{
    alias candidate = f;

    assert(candidate("-123   	+314") == "123314");
}
void main(){}
