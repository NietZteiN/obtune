import std.math;
import std.typecons;
import std.algorithm;
import std.array;

long[] f(long[] container, long cron) 
{
    if (!container.canFind(cron))
        return container;
    auto pref = container[0..container.find(cron).front].dup;
    auto suff = container[container.find(cron).back + 1..$].dup;
    return pref ~ suff;
}
unittest
{
    alias candidate = f;

    assert(candidate([], 2L) == []);
}
void main(){}
