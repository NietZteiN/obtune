#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<long> array, long constant) {
    std::vector<std::string> output = {"x"};
    for (int i = 1; i <= array.size(); i++) {
        if (i % 2 != 0) {
            output.push_back(std::to_string(array[i - 1] * -2));
        } else {
            output.push_back(std::to_string(constant));
        }
    }
    return output;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3})), (-1)) == (std::vector<std::string>({(std::string)"x", (std::string)"-2", (std::string)"-1", (std::string)"-6"})));
}
