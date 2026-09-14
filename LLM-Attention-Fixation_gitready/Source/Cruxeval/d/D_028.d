import std.math;
import std.typecons;
import std.algorithm;

bool f(long[] mylist) 
{
    auto revl = mylist.dup;
    revl.reverse();
    mylist.sort!"a > b";
    return equal(mylist, revl);
}
unittest
{
    alias candidate = f;

    assert(candidate([5L, 8L]) == true);
}
void main(){}
