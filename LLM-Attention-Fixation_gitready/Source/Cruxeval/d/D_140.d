import std.math;
import std.typecons;
import std.algorithm;
import std.array;
import std.string;

string f(string st) 
{
    auto lower_st = st.toLower();
    auto last_h_index = lower_st.lastIndexOf('h');
    auto last_i_index = lower_st.lastIndexOf('i');
    if (last_h_index >= last_i_index)
    {
        return "Hey";
    }
    else
    {
        return "Hi";
    }
}
unittest
{
    alias candidate = f;

    assert(candidate("Hi there") == "Hey");
}
void main(){}
