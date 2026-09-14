#include<assert.h>
#include<bits/stdc++.h>
std::string f(long temp, long timeLimit) {
    long s = timeLimit / temp;
    long e = timeLimit % temp;
    return (s > 1) ? std::to_string(s) + " " + std::to_string(e) : std::to_string(e) + " oC";
}
int main() {
    auto candidate = f;
    assert(candidate((1), (1234567890)) == ("1234567890 0"));
}
