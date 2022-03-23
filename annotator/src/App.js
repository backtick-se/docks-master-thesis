import { useState } from 'react'
import data from './prd_backtick-se_cowait.json'
import styled from 'styled-components'
import ReactMarkdown from 'react-markdown'

const Wrapper = styled('div')`
    display: flex;
    width: 100vw;
    height: 100vh;
    flex-direction: column;
    overflow: hidden;
`

const Foot = styled('div')`
    display: flex;
    justify-content: center;
    padding: 1rem;
`

const Content = styled('div')`
    display: flex;
    flex-grow: 1;
    overflow: hidden;
`

const Section = styled('div')`
    display: flex;
    flex-grow: 1;
    padding: 1rem;
    overflow-y: scroll;
`

const Stats = styled(Section)`
    flex-direction: column;
`

const Features = styled(Section)`
    flex-direction: column;
    width: 30%;
`

const Labels = styled(Section)`
    flex-direction: column;
    width: 30%;
`

const LabelHead = styled('div')`
    display: flex;
    justify-content: space-between;
`

const App = () => {
    const [current, setCurrent] = useState(0)
    const [accepted, setAccepted] = useState([])
    const [rejected, setRejected] = useState([])
    const [docpage, setDocpage] = useState(0)
    const [selected, setSelected] = useState([])

    const next = () => {
        setCurrent(current + 1)
    }

    const onAccept = () => {
        setAccepted([{ ...data[current], selected }, ...accepted])
        setDocpage(0)
        setSelected([])
        next()
        console.log(accepted)
    }

    const onReject = () => {
        setDocpage(0)
        setRejected([data[current], ...rejected])
        setSelected([])
        next()
    }

    const onNextDoc = () => {
        if (docpage + 1 < data[current].contents.length) {
            setDocpage(docpage + 1)
        }
    }

    const onPrevDoc = () => {
        if (docpage > 0) {
            setDocpage(docpage - 1)
        }
    }

    const onRadioChange = (e) => {
        if (selected.includes(docpage)) {
            setSelected(selected.filter((s) => s !== docpage))
        } else {
            setSelected([...selected, docpage])
        }
    }

    return (
        <Wrapper>
            <Content>
                <Stats>
                    <span>
                        <b>Accepted:</b> {accepted.length}
                    </span>
                    <span>
                        <b>Rejected:</b> {rejected.length}
                    </span>
                </Stats>
                {data[current] && (
                    <>
                        <Features>
                            <LabelHead>
                                <span>{data[current].number}</span>
                                <span>
                                    {current + 1} / {data.length}
                                </span>
                            </LabelHead>
                            <h1>{data[current].title}</h1>
                            <div
                                dangerouslySetInnerHTML={{
                                    __html: data[current].body,
                                }}
                            ></div>
                        </Features>
                        <Labels>
                            <LabelHead>
                                <span>
                                    <input
                                        type="radio"
                                        name="docpage"
                                        checked={selected.includes(docpage)}
                                        onClick={onRadioChange}
                                        value={docpage}
                                    />
                                </span>
                                <span>
                                    <button onClick={onPrevDoc}>Prev</button>
                                    &nbsp;
                                    <button onClick={onNextDoc}>Next</button>
                                </span>
                                <span>
                                    {docpage} /{' '}
                                    {data[current].contents.length - 1}
                                </span>
                            </LabelHead>
                            <br />
                            <LabelHead>
                                <span>Selected: {selected}</span>
                            </LabelHead>
                            <ReactMarkdown>
                                {data[current].contents[docpage]}
                            </ReactMarkdown>
                        </Labels>
                    </>
                )}
            </Content>
            <Foot>
                <button onClick={onReject}>Reject</button>
                &nbsp;
                <button onClick={onAccept}>Accept</button>
            </Foot>
        </Wrapper>
    )
}

export default App
