import React from 'react';
import './Loadtesting.css';
import AB from './CS490 screenshots/ab concurrent output.png'
import cpu from './CS490 screenshots/cpu with concurrent.png'
import siege from './CS490 screenshots/siege 1000.png'

const ReleaseNotes = () => {
    return (
        <div className='holder'>
            <div className='load-container'>
                <div className='code-title'>
                    <h1><b>Load testing</b></h1>
                    <a>Load testing is the acting of testing of if a web server can handle the requests incoming. Or figuring out the most practial throughput which is much harder.</a>
                </div>
                <div className='tech-stck'>
                    <h2 className='titles'>Testing the Requests</h2>
                    <p>Testing the web server has multiple options. From the ab command which allows to send requests but only with a single thread thus capping the amount of requests you can send. If you want to test it yourself use <pre><code className='code-block'>$ ab -n 1000 -c 100 http://example.com/</code></pre>
                    This command allows you to send requests of (-n) with a concurrent request of (-c). However this has limiations with the threading in my example it only allows for 1000 requests. Here is an example of what output with this command would look like.</p>
                    <img src={AB} />
                    <p>However, there is a better command for the siege command, with no connection to the siege video game. 
                    Seige allows for multi-threading which send out more requests with not capped unlike ab, the example I used <pre><code className='code-block'> $ siege -c 255 -t 60s http://165.22.39.24/80</code></pre> 
                    To explain what this command does (-c) produces the amount of thread the default limit is 255 since anymore on lower systems would cause crashing. I could push it further but it seemed to prove that my frontend was good.
                    Here is what the command would produce. Along with the cpu usage.</p>
                    <img src={siege}/>
                    <img src={cpu}/>
                    <p>There is some better methods for this which is JMeter however, that requires further setup and for testing right now it the current commadns seem to do the job.
                        Throughput requires more networking with more commands such as networking with wrk2 and modifying it until you get the correct amount you want. 
                        However, with almost 20k requests and a CPU usage of 30% it looks to be enough.
                    </p>
                    <p>For backend, a more cutom approach is required. Such as Selenium, which is an open source tool to test backends. We would use this however, the amount of configuration would be too much for now.
                        Another enterprise choice would be Digital Ocean and expanding with their enterprise solutions since they would also be able to help with configuring it. 
                        Finally, for scaling this website we may be able to switch our plan to scablable plan so we can not worry about the server dying. Only what we can afford. Thank you for read this far.
                    </p>
                </div>
            </div>
            <div className='space'></div>
        </div>
    )
}

export default ReleaseNotes;