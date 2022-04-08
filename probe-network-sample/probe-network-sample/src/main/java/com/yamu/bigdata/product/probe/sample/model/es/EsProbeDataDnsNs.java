package com.yamu.bigdata.product.probe.sample.model.es;

import com.yamu.bigdata.product.probe.sample.model.*;

import java.util.ArrayList;

/**
 * dns-dnsNSHijack 的 es日志
 */
public class EsProbeDataDnsNs extends EsProbeDataDns {

    public EsProbeDataDnsNs(
            String taskProbingId,
            ProbeTask probeTask,
            ProbeDevice probeDevice,
            ProbeResult probeResult) {
        super(taskProbingId, probeTask, probeDevice, probeResult);
    }

    @Override
    protected void putAnswer(ProbeResultDns probeResultDns) {
        this.answer = new ArrayList<>();
        for (ProbeResultDnsSection section: probeResultDns.answerSection.getSections()) {
            if (section.rdtype.equals(probeResultDns.rrtype)) {
                EsProbeDataDnsAnswerNs dnsAnswerNs = new EsProbeDataDnsAnswerNs(section.result);
                ProbeResultDnsSectionNs sectionNs = (ProbeResultDnsSectionNs) section;
                ArrayList<String> results_a = new ArrayList<>();
                for (ProbeResultDns innerProbeResultDns: sectionNs.resultsA) {
                    ArrayList<String> innerA = innerProbeResultDns.answerSection.getSectionsWithRdtype("A");
                    for (String s: innerA) {
                        results_a.add(s);
                    }
                }
                dnsAnswerNs.results_a = results_a;
                this.answer.add(dnsAnswerNs);
            }
        }
    }

}
