#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<long> array) {
    std::vector<std::string> just_ns;
    std::transform(array.begin(), array.end(), std::back_inserter(just_ns), [](long num) {
        return std::string(num, 'n');
    });
    
    std::vector<std::string> final_output;
    for (const std::string& wipe : just_ns) {
        final_output.push_back(wipe);
    }
    
    return final_output;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>())) == (std::vector<std::string>()));
}
