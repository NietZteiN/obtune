#include<assert.h>
#include<bits/stdc++.h>
std::vector<float> f(std::vector<long> numbers) {
    std::vector<float> floats;
    for (auto n : numbers) {
        floats.push_back(n - floor(n));
    }
    if (std::find(floats.begin(), floats.end(), 1.0) != floats.end()) {
        return floats;
    } else {
        return std::vector<float>();
    }
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)100, (long)101, (long)102, (long)103, (long)104, (long)105, (long)106, (long)107, (long)108, (long)109, (long)110, (long)111, (long)112, (long)113, (long)114, (long)115, (long)116, (long)117, (long)118, (long)119}))) == (std::vector<float>()));
}
