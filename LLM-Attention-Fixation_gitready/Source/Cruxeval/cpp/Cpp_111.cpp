#include<assert.h>
#include<bits/stdc++.h>
std::tuple<long, long> f(std::map<std::string,long> marks) {
    long highest = 0;
    long lowest = 100;
    for (const auto& pair : marks) {
        long value = pair.second;
        if (value > highest) {
            highest = value;
        }
        if (value < lowest) {
            lowest = value;
        }
    }
    return std::make_tuple(highest, lowest);
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"x", 67}, {"v", 89}, {"", 4}, {"alij", 11}, {"kgfsd", 72}, {"yafby", 83}}))) == (std::make_tuple(89, 4)));
}
