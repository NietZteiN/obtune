import std.math;
import std.typecons;
string f(string perc, string full) 
{
    string reply = "";
    size_t i = 0;
    while (i < perc.length && i < full.length && perc[i] == full[i]) {
        if (perc[i] == full[i]) {
            reply ~= "yes ";
        } else {
            reply ~= "no ";
        }
        i++;
    }
    return reply;
}
unittest
{
    alias candidate = f;

    assert(candidate("xabxfiwoexahxaxbxs", "xbabcabccb") == "yes ");
}
void main(){}
