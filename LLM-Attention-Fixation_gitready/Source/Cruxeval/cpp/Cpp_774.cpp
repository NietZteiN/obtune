#include<assert.h>
#include<bits/stdc++.h>
std::string f(long num, std::string name) {
    std::stringstream ss;
    ss << "quiz leader = " << name << ", count = " << num;
    return ss.str();
}
int main() {
    auto candidate = f;
    assert(candidate((23), ("Cornareti")) == ("quiz leader = Cornareti, count = 23"));
}
