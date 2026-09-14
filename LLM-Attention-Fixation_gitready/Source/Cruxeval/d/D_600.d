import std.math;
import std.typecons;
import std.array;
import std.conv;

string repeatString(string str, size_t times) {
    string result = "";
    foreach (_; 0 .. times) {
        result ~= str;
    }
    return result;
}

string[] f(long[] array) 
{
    string[] just_ns;
    foreach (num; array) {
        just_ns ~= repeatString("n", num);
    }
    string[] final_output;
    foreach (wipe; just_ns) {
        final_output ~= wipe;
    }
    return final_output;
}
unittest
{
    alias candidate = f;

    assert(candidate([]) == []);
}
void main(){}
